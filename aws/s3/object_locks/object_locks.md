# Note: I am not doing this in the command line b/c I don't want a file I can't delete

## Create a new folder

`aws s3 mb s3://object-lock-fun`

## Turn on object locking

```
aws s3api put-object-lock-configuration \
    --bucket object-lock-fun \
    --object-lock-configuration '{ "ObjectLockEnabled": "Enabled", "Rule": { "DefaultRetention": { "Mode": "COMPLIANCE", "Days": 50 }}}'
```

or you can do the following with GOVERNANCE
## NOTE: YOU MUST ENABLE VERSIONING

`aws s3api put-bucket-versioning --bucket object-lock-fun --versioning-configuration Status=Enabled`

```
aws s3api put-object-lock-configuration \
    --bucket my-bucket-with-object-lock \
    --object-lock-configuration '{ "ObjectLockEnabled": "Enabled", "Rule": { "DefaultRetention": { "Mode": "GOVERNANCE", "Days": 50 }}}'
```

## New file and upload (this is the file we will test-remove)

`echo 'this-is-the-gov' > gov.txt`

`aws s3 cp gov.txt s3://object-lock-fun`

## The thing to know is that you can delete this file but others can't

`aws s3api list-object-versions --bucket object-lock-fun --key gov.txt`

## Delete the version file (this is the way)

`aws s3api delete-object --bucket= 'object-lock-fun' --key='gov.txt' --version-id='EXhrs....etc...' --bypass-governance-retention`

## Use compliance mode for s3 object

`aws s3api put-object --bucket='object-lock-fun' --key 'gov.txt' --body='compliance.txt' --object-lock-mode=COMPLIANCE --object-lock-retain-until-date='2024-11-19T00:00:00Z'`

## Try and delete different versions

`aws s3api list-object-versions --bucket='object-lock-fun' --key= 'gov.txt' --version-id='AbdcGhhaz.etc.'`

### New file

`touch legal.txt`

`aws s3 copy legal.txt s3://object-lock-fun/legal.txt`

`aws s3api put-object-legal-hold --bucket 'object-lock-fun' --key 'legal.txt' --legal-hold status=ON`

`aws s3 rm s3://object-lock-fun/legal.txt`

`aws s3api list-object-versions --bucket object-lock-fun/legal.txt`

`aws s3 api list-object-versions --bucket object-lock-fun`

Now we cannot delete

`awsw s3api delete-object --bucket 'object-lock-fun' --key 'legal.txt' --version-id 'limcfjc..et...'`

Turn the legal hold off - Make sur IAM policy allows this- note version-id's are gibberish

``aws s3api put-object-legal-hold --bucket 'object-lock-fun' --version-id='hdbbfhdjjsjsjlks_' --key 'legal.txt' --legal-hold status=OFF``
