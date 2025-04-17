variable "developer_users" {
  description = "List of IAM users who can assume the developer role"
  type        = list(string)
  default     = ["user1", "user2"] # Replace with actual developer IAM users
}

variable "allowed_account_id" {
  description = "The AWS Account ID where this is being deployed"
  type        = string
  default     = ""
}
