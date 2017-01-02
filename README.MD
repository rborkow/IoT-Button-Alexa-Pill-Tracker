# Pill Tracker App for Alexa & AWS IoT Button

Quick app for using an AWS IoT button and Amazon Alexa to keep track of the last time you took pills/vitamins/whatever.

## Requirements
- [1 AWS IoT Button](https://aws.amazon.com/iotbutton/)
- 1 DynamoDB instance
- AWS Lambda function for powering the Alexa Skill

## Setup

### IoT Button Setup
1. Follow the instructions [here](https://aws.amazon.com/iotbutton/getting-started/) to get your button configured and set up. **Be sure to add your button in a region that supports Alexa Skills. I recommend "US East (N. Virginia)".**
2. Go to the [AWS IoT Rule Hub](https://console.aws.amazon.com/iotv2/home?region=us-east-1#/rulehub) and create a new rule.
3. Give your rule any name and description you'd like.
4. Select the _2016-03-23_ SQL version
5. Set "*" as the attribute, and "iotbutton/<YOUR BUTTON'S SERIAL NUMBER>" as the topic filter. You can get your serial number from the back of your button, or from the example rule created in the setup process.
6. Press "Add Action" to create a new action for this rule.
7. Select the "Insert a message into a DynamoDB table" action.
8. Use the "Create a new resource" action to create a new DynamoDB table.
9. Create a table:
    10. Name: "pillbutton_presses"
    11. Partition Key: SerialNumber (String type)
    12. Sort key: Timestamp (Number type)
    13. Use default settings: Checked
14. Go back to the action configuration page, and refresh the list of Dynamo DB tables
15. Select the "pillbutton_presses" table.
16. Set the following parameters:
    17. Hash key values: "${SerialNumber}"
    18. Sort key values: "${timestamp()}"
19. Create a new IAM role and press the button to allow AWS to set the correct permissions.

### Alexa Skill Lambda Function Setup
For a general overview of setting up a custom Alexa skill using AWS lambda, see the documentation [here](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/developing-an-alexa-skill-as-a-lambda-function).

This guide will walk you through most of the steps necessary to get a Lambda function set up as a back-end to the Alexa Skill. Two additional steps will be needed to get the function running correctly:
1. Once an IAM Role is created for the skill, find the role in the IAM console and attach the "AmazonDynamoDBReadOnlyAccess" policy.
2. On the function page for your Lambda function, add an environmental variable named "SerialNumber" and set the value to the serial number of your AWS IoT button.

### Alexa Skill Registration
**Note: You must register this skill with the same Amazon account as your Echo in order it to be enabled on your device.**

An overview of registering an Alexa skill for use with your Echo are available [here](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/registering-and-managing-alexa-skills-in-the-developer-portal).

When you get to the interaction model setup, you can use the following as intents and utterances:

**Intent**
```javascript
{
  "intents": [
    {
      "intent": "HoursAgoIntent"
    },
    {
      "intent": "AMAZON.HelpIntent"
    }
  ]
}
```

***Utterances**
```
HoursAgoIntent how many hours ago did i take my vitamins
HoursAgoIntent how many hours ago did i take my pills
HoursAgoIntent when did i last take my vitamins
HoursAgoIntent when did i last take vitamins
HoursAgoIntent when i last took vitamins
HoursAgoIntent when i last took my vitamins
HoursAgoIntent did i take my vitamins today
HoursAgoIntent did i take my vitamins tonight
HoursAgoIntent did i take my vitamins this morning
HoursAgoIntent did i take my vitamins recently
```
