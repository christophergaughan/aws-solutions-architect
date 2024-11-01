## Create a new folder
`aws s3 mb s3://objec-lock-clg`

## Turn on object locking

```
aws s3api put-onject-lock-configuration \
-- bucket my-bucket-with-object-lock \
-- object-lock-configuration '{"Object-Enabled: "Enabled", "Rule": {"Deafault:Retention":{"Mode":"COMPLIANCE", "Days":50}}}'
```
