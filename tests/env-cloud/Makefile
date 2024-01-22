.PHONY: plan
plan: init
	terraform fmt
	@touch ./.env
	source ./.env && terraform plan

.PHONY: apply
apply: init
	terraform fmt
	@touch ./.env
	source ./.env && terraform apply -auto-approve

.PHONY: init
init: .terraform
.terraform:
	terraform init

.PHONY: clean
clean:
	rm -rf .terraform
	rm -f .terraform.lock.hcl

.PHONY: destroy
destroy:
	@touch ./.env
	source ./.env && terraform destroy -auto-approve

test-connectivity:
	ansible -i ./inventory -m ping all
