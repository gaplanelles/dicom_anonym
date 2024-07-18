resource "oci_core_subnet" "subnet" {
  for_each = { for subnet in local.subnets_with_labels : subnet.name => subnet }
  
  compartment_id = oci_identity_compartment.net_subcompartment.id
  vcn_id         = oci_core_vcn.vcn.id
  cidr_block     = each.value.cidr_block
  display_name   = each.value.display_name
  dns_label      = each.value.dns_label
  
  prohibit_internet_ingress  = each.value.name == "web" ? false : true
  prohibit_public_ip_on_vnic = each.value.name == "web" ? false : true
  
  dhcp_options_id   = oci_core_default_dhcp_options.dhcp_options.id
  route_table_id    = oci_core_route_table.route_table.id
  security_list_ids = [
    oci_core_security_list.custom_security_list.id,
    oci_core_default_security_list.default_security_list.id
  ]
}

output "subnet_ids" {
  value = {
    for name, subnet in oci_core_subnet.subnet :
    name => {
      id           = subnet.id
      display_name = subnet.display_name
    }
  }
}
