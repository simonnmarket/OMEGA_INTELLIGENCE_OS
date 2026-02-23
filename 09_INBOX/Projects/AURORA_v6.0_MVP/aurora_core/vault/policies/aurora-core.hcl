path "secret/data/aurora/*" {
  capabilities = ["read", "list"]
}

path "secret/metadata/aurora/*" {
  capabilities = ["list"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

