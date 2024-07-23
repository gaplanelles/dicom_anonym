data "oci_objectstorage_namespace" "container_namespace" {
  compartment_id = oci_identity_compartment.app_subcompartment.id
}

# namespace             = data.oci_objectstorage_namespace.container_namespace.namespace
# Replacing the line above with the line below:
# namespace             = var.namespace

resource "oci_objectstorage_bucket" "dicom_bucket" {
  namespace             = var.namespace # 
  name                  = var.dicom_bucket_name
  compartment_id        = oci_identity_compartment.app_subcompartment.id
  storage_tier          = "Standard"
  auto_tiering          = "Disabled"
  versioning            = "Disabled"
  object_events_enabled = "false"
}

resource "oci_objectstorage_bucket" "txt_bucket" {
  namespace             = var.namespace # 
  name                  = var.txt_bucket_name
  compartment_id        = oci_identity_compartment.app_subcompartment.id
  storage_tier          = "Standard"
  auto_tiering          = "Disabled"
  versioning            = "Disabled"
  object_events_enabled = "false"
}

# terraform is not creating folders in a bucket
# that are needed for anonymization services to work

output "dicom_bucket_name" {
  value = oci_objectstorage_bucket.dicom_bucket.name
}


output "txt_bucket_name" {
  value = oci_objectstorage_bucket.txt_bucket.name
}
