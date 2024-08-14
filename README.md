
# What Does this Project do?
Phoenix bank management system is a secure platform offering various banking operations. 
Upon launching, you'll encounter the main menu with options ranging from
- creating a new account to 
- managing existing ones, 
- conducting deposits and withdrawals,
- transferring funds, 
- accessing the manager's menu for additional functionalities,
- deleting accounts, and finally, exiting the application.

# Why did i do this?
 project for CBSE 12th IP

This is a very basic Bank Management System 
It took me about 2 weeks to complete the whole thing, and another 1 week to refine the code

# Requirements
--> VScode or Spyder
--> MySQL

for more details look into the attached pdf, i have provided the flowchart of the code and the output
the pdf is more of a readme than this read me document

# Project Flow Chart
![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)
![alt text](image-5.png)
![alt text](image-6.png)
![alt text](image-7.png)

# Program Output

(note - dummy values have been used throughout this sample program output)

Login (Establishing Connection)
This part is about SQL,
- Kindly insert the accurate information about your SQL
![alt text](image-8.png)

Main Menu
- Main Menu along with the connection part
![alt text](image-9.png)

Option_1 (To Create an Account)
- If In Case Password isn’t Strong Enough, or It doesn’t meet the requirement
![alt text](image-10.png)

- If Password is Suitable and Strong Enough
![alt text](image-11.png)

Option_2 (To View the Details of an Account)
- When the correct password is entered
![alt text](image-12.png)

- When the Wrong password is entered
![alt text](image-13.png)

Option_3 (To Deposit into an Account)
Note – For Depositing into an Account Password is not required (Unlike Withdrawing from an Account)
- If Account Holder Wishes to Donate to Charity
![alt text](image-14.png)

- If Account Holder Doesn’t want to Donate to Charity
![alt text](image-15.png)

Option_4 (To Withdraw From an Account)
- Withdrawing Amount
![alt text](image-16.png)

- Withdrawing more Amount than balance in bank
![alt text](image-17.png)

- Withdrawing Exactly Total Amount of balance in Bank
![alt text](image-18.png)

Option_5 (To Perform a Bank Transfer from One Account to Another)
- While both senders and receivers account exists and the sender account has sufficient fund
![alt text](image-19.png)

- When senders account number is entered wrongly (same occurs when receivers account number is inserted wrongly)
![alt text](image-20.png)

Option_6 (Manager’s Menu)
A Whole Bunch of Exclusive features for Managing the Bank
- The managers menu, When correct password is entered
![alt text](image-21.png)

- When wrong password is entered for 3 times
It automatically ends the program and proceeds to warn the user that it is about to contact the authorities
![alt text](image-22.png)

Option_1 (Manager’s Menu)
- To view Account Details with Account Specific Log Entries
Here status denotes if the account is locked or not,
(if status is = 0 then it is usable), (if status is = 1 then it is locked)
(The account automatically gets locked when wrong password is entered 3 times)
![alt text](image-23.png)

Option_2 (Manager’s Menu)
- To View All The Existing Account Holders In the Bank
![alt text](image-24.png)

Option_3 (Manager’s Menu)
- To view Past Customers/Account Holders
![alt text](image-25.png)

Option_4 (Manager’s Menu)
- To view All Recorded Log Entries
![alt text](image-26.png)

Option_5 (Manager’s Menu)
To Reset Password for a locked Account or If Account Holder Forgot Password
- If passwords doesn’t match
![alt text](image-27.png)

- If passwords match
![alt text](image-28.png)

Option_6 (Manager’s Menu)
- To Exit Manager’s Menu
![alt text](image-29.png)

Option_7 (Delete an Account)
- The deleted account’s get recorded in the previous account’s table
![alt text](image-30.png)

Option_8 (To Exit Phoenix Bank Management System)
![alt text](image-31.png)
