resource "oci_core_default_dhcp_options" "dhcp_options" {
  compartment_id             = oci_identity_compartment.net_subcompartment.id
  display_name               = "${var.project_name}-default-dhcp-options"
  domain_name_type           = "CUSTOM_DOMAIN"
  manage_default_resource_id = oci_core_vcn.vcn.default_dhcp_options_id

  options {
    type    = "DomainNameServer"
    server_type = "VcnLocalPlusInternet"
  }

  options {
    type    = "SearchDomain"
    search_domain_names = ["${local.dns_label}.oraclevcn.com"]
  }
}

output "default_dhcp_options_id" {
  value = oci_core_default_dhcp_options.dhcp_options.id
}
