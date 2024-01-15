.PHONY: apply
apply: init
	terraform fmt
	terraform apply -auto-approve

.PHONY: init
init: .terraform
.terraform:
	terraform init

clean:
	rm -rf .terraform
	rm -f .terraform.lock.hcl

destroy:
	terraform destroy -auto-approve
