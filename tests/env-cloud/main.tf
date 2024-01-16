provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_compute_zones" "this" {
  region  = var.region
  project = var.project_id
}

locals {
  type  = ["public", "private"]
  zones = data.google_compute_zones.this.names
}

#---

# === VPC ===
# Set CIDR to 10.0.2.0/24
# CIDR = Classless Inter-Domain Routing
resource "google_compute_network" "this" {
  name                            = "${var.name}-vpc"
  delete_default_routes_on_create = false
  routing_mode                    = "GLOBAL"
  auto_create_subnetworks         = false
}

# Peering with the VPC 'luiz-aap-net'
# datasource for the VPC 'luiz-aap-net'
# data "google_compute_network" "peer" {
#   name = "luiz-aap-net"
# }
# resource "google_compute_network_peering" "peering-out" {
#   name         = "${var.name}-vpc-peering-out"
#   network      = google_compute_network.this.id
#   peer_network = data.google_compute_network.peer.id
# }
# resource "google_compute_network_peering" "peering-in" {
#   name         = "${var.name}-vpc-peering-in"
#   network      = data.google_compute_network.peer.id
#   peer_network = google_compute_network.this.id
# }



# === Subnets ===
# From CIDR 10.0.1.0/24 to 10.0.2.0/24
resource "google_compute_subnetwork" "sub0" {
  name          = "${var.name}-subnet-0"
  ip_cidr_range = "10.0.1.0/24"
  network       = google_compute_network.this.id
  region        = var.region
}
resource "google_compute_subnetwork" "sub1" {
  name          = "${var.name}-subnet-1"
  ip_cidr_range = "10.0.2.0/24"
  network       = google_compute_network.this.id
  region        = var.region
}


# === Firewall rules ===
# Allow everything from anywhere
resource "google_compute_firewall" "this" {
  name    = "${var.name}-firewall"
  network = google_compute_network.this.id

  allow {
    protocol = "all"
    # ports    = ["1-65535"]
  }

  source_ranges = ["0.0.0.0/0"]
}


#---

# === Service Account ===
# TODO

# === Instances ===
# x86 machine
resource "google_compute_instance" "x86-0" {
  name                      = "${var.name}-x86-0"
  machine_type              = "n2-standard-2"
  zone                      = local.zones[0]
  allow_stopping_for_update = true
  deletion_protection       = false

  # prevent machine from being recreated
  lifecycle {
    # create_before_destroy = true
    ignore_changes = [
      machine_type,
      boot_disk,
      scratch_disk,
      network_interface,
      metadata,
      metadata_startup_script,
      service_account,
    ]
  }

  boot_disk {
    initialize_params {
      # RHEL9
      image = "rhel-9"
      labels = {
        my_label = "value"
      }
    }
  }

  // Local SSD disk
  scratch_disk {
    interface = "NVME"
  }

  network_interface {
    network    = google_compute_network.this.id
    subnetwork = google_compute_subnetwork.sub1.id

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    foo = "bar"
  }

  metadata_startup_script = "echo hi > /test.txt"

  # service_account {
  #   # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
  #   email  = google_service_account.default.email
  #   scopes = ["cloud-platform"]
  # }
}

# arm64 machine
resource "google_compute_instance" "arm64-0" {
  name                      = "${var.name}-arm64-0"
  machine_type              = "t2a-standard-4"
  zone                      = local.zones[0]
  allow_stopping_for_update = true
  deletion_protection       = false

  # prevent machine from being recreated
  lifecycle {
    # create_before_destroy = true
    ignore_changes = [
      machine_type,
      boot_disk,
      scratch_disk,
      network_interface,
      metadata,
      metadata_startup_script,
      service_account,
    ]
  }

  boot_disk {
    initialize_params {
      # RHEL9
      image = "rhel-9-arm64"
      labels = {
        my_label = "value"
      }
    }
  }

  // Local SSD disk
  # scratch_disk {
  #   interface = "NVME"
  # }

  network_interface {
    network    = google_compute_network.this.id
    subnetwork = google_compute_subnetwork.sub1.id

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    foo = "bar"
  }

}




# output.tf
output "network" {
  # map [id, name]
  value = {
    id   = google_compute_network.this.id
    name = google_compute_network.this.name
  }
}

output "subnets" {
  # list of maps [id, name, cidr_range]
  value = [
    {
      id         = google_compute_subnetwork.sub0.id
      name       = google_compute_subnetwork.sub0.name
      cidr_range = google_compute_subnetwork.sub0.ip_cidr_range
    },
    {
      id         = google_compute_subnetwork.sub1.id
      name       = google_compute_subnetwork.sub1.name
      cidr_range = google_compute_subnetwork.sub1.ip_cidr_range
    },
  ]
}

# === SSH script ===
# Create local file ./instance-ssh.sh
output "ssh" {
  value = "${path.module}/instance-ssh.sh"
}

# Create template variable
data "template_file" "instance-ssh-script" {
  template = <<-EOT
#!/bin/bash
gcloud compute ssh --project ${var.project_id} --zone ${local.zones[0]} ${google_compute_instance.x86-0.name}
EOT
}

# Write template to file
resource "local_file" "instance-ssh-script" {
  content  = data.template_file.instance-ssh-script.rendered
  filename = "${path.module}/instance-ssh.sh"
}

# Make file executable
resource "null_resource" "instance-ssh-script" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = <<-EOF
    set -x
    chmod +x '${path.module}/instance-ssh.sh'
    gcloud compute config-ssh
EOF
  }

  depends_on = [
    local_file.instance-ssh-script,
  ]
}



# === Ansible Inventory ===

# Create local file ./inventory
output "inventory" {
  value = "${path.module}/inventory"
}
data "template_file" "inventory" {
  # host pattern: <instance_name>.<instance_zone>.<project_id>
  template = <<-EOT
[all]
${google_compute_instance.x86-0.name}.${google_compute_instance.x86-0.zone}.${var.project_id}
${google_compute_instance.arm64-0.name}.${google_compute_instance.arm64-0.zone}.${var.project_id}

[all:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOT
}
resource "local_file" "inventory" {
  content  = data.template_file.inventory.rendered
  filename = "${path.module}/inventory"

}
