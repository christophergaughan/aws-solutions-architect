## make a bucket

`aws s3 mb s3://metadata-bucket-clg`

### Create a new file

`echo "hello mars" > hello.txt`

### Upload file with metadata
`aws s3api put-object --bucket metadata-bucket-clg --key hello.txt --body=hello.txt --metadata Planet=Mars`

### Now we get the metadata through **head object**
`aws s3api head-object --bucket metadata-bucket-clg --key hello.txt`

## Some Rules with AWS maetadata:
You can set object metadata in Amazon S3 at the time you upload the object. Object metadata is a set of name-value pairs. After you upload the object, **you cannot modify object metadata**. The only way to modify object metadata is to *make a copy* of the object and set the metadata.

When you create an object, you also specify the key name, which uniquely identifies the object in the bucket. The object key (or key name) uniquely identifies the object in an Amazon S3 bucket. For more information, see Naming Amazon S3 objects.

There are two kinds of metadata in Amazon S3: system-defined metadata and user-defined metadata. The following sections provide more information about system-defined and user-defined metadata. For more information about editing metadata using the Amazon S3 console, see Editing object metadata in the Amazon S3 console.

## Cleanup
`1aws s3 rm s3://metadata-bucket-clg/hello.txt`