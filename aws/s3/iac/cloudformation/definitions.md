# 1) Execute change set
### In AWS CloudFormation, an execution of a changeset refers to the process of applying a set of proposed changes to an existing CloudFormation stack. A changeset is essentially a summary that outlines how your stack will be modified if you proceed with an update. It allows you to preview the impact of changes—such as adding, modifying, or deleting resources—before actually implementing them.

**Here's how it works:**

* Create a Changeset: When you want to update a stack, you start by creating a changeset. This involves providing a new or modified CloudFormation template that specifies the desired state of your AWS resources.

* Review the Changeset: CloudFormation compares the existing stack with the new template and generates a changeset. This changeset lists all the proposed changes, allowing you to review what will happen if you proceed.

* Execute the Changeset: After reviewing and confirming that the changes are acceptable, you execute the changeset. This action tells CloudFormation to apply the changes outlined in the changeset to your stack.

**Why Use Changesets?**

* Risk Mitigation: By previewing changes before execution, you can avoid unintended modifications that might disrupt your environment.

* Transparency: Changesets provide a clear and detailed view of what resources will be affected and how.

* Control: They give you the ability to manage and orchestrate updates in a controlled manner.
Example Scenario:

Suppose you have a stack that sets up an EC2 instance and an S3 bucket. You want to update the stack to add a new IAM role. By creating a changeset, you can see that the update will add the IAM role without affecting the existing EC2 instance and S3 bucket. Once you're satisfied, you execute the changeset to apply the update.

Key Points:

Changesets are optional but recommended for updating stacks, especially in production environments.
Executing a changeset is irreversible; once executed, the changes will be applied to your stack.
If you don't execute the changeset, the proposed changes won't affect your stack.
References:

AWS CloudFormation Changesets Documentation
By using the "Execute Changeset" feature, you ensure that updates to your AWS resources are intentional, well-understood, and safely applied.