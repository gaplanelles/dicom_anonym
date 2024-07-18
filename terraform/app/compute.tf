data "oci_identity_availability_domain" "ad" {
  compartment_id = var.compartment_id
  ad_number      = 1
}

data "oci_core_images" "ubuntu_image" {
  compartment_id           = var.compartment_id
  operating_system         = var.instance_image_os
  operating_system_version = var.instance_image_version
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_instance" "app_instance" {
  availability_domain = data.oci_identity_availability_domain.ad.name
  compartment_id      = oci_identity_compartment.app_subcompartment.id
  shape               = var.instance_shape
  display_name        = "${var.project_name}-app-instance"
  state               = "RUNNING"

  metadata = {
    ssh_authorized_keys = join("\n", [
      for key_file in fileset("${path.module}/keys", "*.pub"):
        file("${path.module}/keys/${key_file}")
    ])
  }
  
  agent_config {
    are_all_plugins_disabled = "false"
    is_management_disabled   = "false"
    is_monitoring_disabled   = "false"
    plugins_config {
      desired_state = "DISABLED"
      name          = "Vulnerability Scanning"
    }
    plugins_config {
      desired_state = "DISABLED"
      name          = "Management Agent"
    }
    plugins_config {
      desired_state = "ENABLED"
      name          = "Custom Logs Monitoring"
    }
    plugins_config {
      desired_state = "DISABLED"
      name          = "Compute RDMA GPU Monitoring"
    }
    plugins_config {
      desired_state = "ENABLED"
      name          = "Compute Instance Monitoring"
    }
    plugins_config {
      desired_state = "DISABLED"
      name          = "Compute HPC RDMA Auto-Configuration"
    }
    plugins_config {
      desired_state = "DISABLED"
      name          = "Compute HPC RDMA Authentication"
    }
    plugins_config {
      desired_state = "ENABLED"
      name          = "Cloud Guard Workload Protection"
    }
    plugins_config {
      desired_state = "DISABLED"
      name          = "Block Volume Management"
    }
    plugins_config {
      desired_state = "DISABLED"
      name          = "Bastion"
    }
  }

  create_vnic_details {
    display_name           = replace(var.sanitized_project_name, "_", "-")
    hostname_label         = replace(var.sanitized_project_name, "_", "-")
    subnet_id              = var.subnet_id
    private_ip             = var.private_ip
  }

  shape_config {
    memory_in_gbs             = "16"
    ocpus                     = "1"
  }
  
  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_image.images[0].id
  }
  
}

resource "null_resource" "provisioner" {
  triggers = {
    always_run = "${timestamp()}"
  }

  connection {
    type        = "ssh"
    host        = "${oci_core_instance.app_instance.public_ip}"
    timeout     = "5m"
    user        = "ubuntu"
    private_key = "${file("${var.ssh_key_file}")}"
  }

  provisioner "file" {
    source      = var.oci_config_dir
    destination = "/home/ubuntu/.oci"
  }

  provisioner "file" {
    source      = "${path.module}/../../../dicom_anonym"
    destination = "/home/ubuntu/dicom_anonym"
  }

  provisioner "file" {
    source      = "${path.module}/scripts"
    destination = "/home/ubuntu/scripts"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod -R +x ~/scripts",
      "mkdir -p ~/logs/install ~/logs/service",
      "/bin/bash -c '~/scripts/install/00_upgrade_os.sh 2>&1 | tee ~/logs/install/00_upgrade_os.log'",
      "/bin/bash -c '~/scripts/install/01_install_forge.sh 2>&1 | tee ~/logs/install/01_install_forge.log'",
      "/bin/bash -c -i '~/scripts/install/02_create_conda.sh ${var.sanitized_project_name} 2>&1 | tee ~/logs/install/02_create_conda.log'", # -i (interactive mode) is required, as otherwise conda setup from .bashrc won't be used
      "/bin/bash -c '~/scripts/install/03_create_service.sh ${var.sanitized_project_name} anonym_backend backend_ikard/anonym_backend.py 2>&1 | tee ~/logs/install/03_create_service_anonym_backend.log'",
      "/bin/bash -c '~/scripts/install/03_create_service.sh ${var.sanitized_project_name} txt_anonymizer_backend text_anonymizer/txt_anonymizer_backend.py 2>&1 | tee ~/logs/install/03_create_service_txt_anonymizer_backend.log'",
      "/bin/bash -c '~/scripts/install/04_modify_config.sh ${var.compartment_id} ${var.namespace} ${var.txt_bucket_name} 2>&1 | tee ~/logs/install/04_modify_config.log'",
    ]
  }
}

output "app_instance_id" {
  value = oci_core_instance.app_instance.id
}

output "app_instance_public_ip" {
  value = oci_core_instance.app_instance.public_ip
}
