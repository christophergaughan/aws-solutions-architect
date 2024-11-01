# Note:

To modify the metadata of an object in Amazon S3, you need to copy the object and set the new metadata during the copy operation. This process effectively replaces the existing object with a new version that includes the updated metadata. Here’s how you can do it using the AWS Command Line Interface (CLI):

Steps to Modify Object Metadata:
Copy the object: Use the aws s3api copy-object command, which allows you to copy an existing object within S3 and set or update its metadata during the process.
Set metadata: Specify the new metadata using the --metadata flag. If you want to preserve the existing metadata while adding new ones, use the --metadata-directive flag with the value REPLACE.
Example Command:
aws s3api copy-object \
    --bucket your-bucket-name \
    --copy-source your-bucket-name/your-object-key \
    --key your-object-key \
    --metadata-directive REPLACE \
    --metadata "x-amz-meta-newkey=newvalue"
Explanation:
--bucket: The bucket where the copied object will reside.
--copy-source: Specifies the source object in the format bucket-name/object-key.
--key: The key (or name) for the new object (can be the same as the original).
--metadata-directive: This option determines whether the metadata is copied from the source object or replaced with new metadata. Use REPLACE to overwrite the metadata.
--metadata: The new metadata you want to add.
Important Points:
Overwriting Metadata: When you use --metadata-directive REPLACE, any existing metadata on the object is not preserved unless explicitly included in the new --metadata definition.
Preserving Data: This operation keeps the object content the same but changes the metadata as specified.
Example Scenario:
Suppose you have an object named document.txt in a bucket called my-bucket and want to add or modify a custom metadata key called x-amz-meta-category:

aws s3api copy-object \
    --bucket my-bucket \
    --copy-source my-bucket/document.txt \
    --key document.txt \
    --metadata-directive REPLACE \
    --metadata "x-amz-meta-category=report"
This command makes a copy of document.txt in the same bucket with updated metadata.

Additional Note:
If you need to copy objects across different buckets or use different access permissions, you can add flags like --acl for access control and specify different buckets in the --copy-source argument.



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