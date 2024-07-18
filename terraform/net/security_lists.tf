resource "oci_core_security_list" "custom_security_list" {
  compartment_id = oci_identity_compartment.net_subcompartment.id
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "${var.sanitized_project_name}-custom-security-list"

  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    stateless   = "false"
    tcp_options {
      max = "3000"
      min = "3000"
    }
  }

  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    stateless   = "false"
    tcp_options {
      max = "2053"
      min = "2053"
    }
  }

  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    stateless   = "false"
    tcp_options {
      max = "2055"
      min = "2055"
    }
  }
}

resource "oci_core_default_security_list" "default_security_list" {
  compartment_id             = oci_identity_compartment.net_subcompartment.id
  display_name               = "${var.sanitized_project_name}-default-security-list"
  manage_default_resource_id = oci_core_vcn.vcn.default_security_list_id
  
  egress_security_rules {
    destination      = "0.0.0.0/0"
    destination_type = "CIDR_BLOCK"
    protocol  = "all"
    stateless = "false"
  }
  ingress_security_rules {
    protocol    = "6"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    stateless   = "false"
    tcp_options {
      max = "22"
      min = "22"
    }
  }
  ingress_security_rules {
    icmp_options {
      code = "4"
      type = "3"
    }
    protocol    = "1"
    source      = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
    stateless   = "false"
  }
  ingress_security_rules {
    icmp_options {
      code = "-1"
      type = "3"
    }
    protocol    = "1"
    source      = "10.0.23.0/24"
    source_type = "CIDR_BLOCK"
    stateless   = "false"
  }
}

output "custom_security_list_id" {
  value = oci_core_security_list.custom_security_list.id
}

output "default_security_list_id" {
  value = oci_core_default_security_list.default_security_list.id
}
