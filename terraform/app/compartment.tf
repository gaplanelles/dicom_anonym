resource "oci_identity_compartment" "app_subcompartment" {
  name           = "${var.sanitized_project_name}_app"
  description    = "Application subcompartment for ${var.project_name}"
  compartment_id = var.compartment_id
  depends_on     = [var.net_subcompartment_id]
}

output "app_subcompartment_id" {
  value = oci_identity_compartment.app_subcompartment.id
}
