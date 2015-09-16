README
======

Set up
---------------

Test users:

  Email             | Name        | Registered  | Memo
  ------------------|-------------|-------------|---------------------------------
  test@servuno.com  | John Smith  | Yes         | All purpose test user; sleeping bears; family helpers
  test1@servuno.com | Test1 Bot   | Yes         | Secondary user to test; sleeping bears.
  test2@servuno.com | Nancy Doe   | Yes         | is staff and thus is able to bypass some limitations. doesn't have many contacts (is_isolated=True); not sleeping bears
  test3@servuno.com | N/A         | No          | Test pre-registered user, always remain unsigned up
  test4@servuno.com | Jack Lee    | Yes         | Set up with fixed testing data (e.g., favors). Don't remove any data related to test3
  test5@servuno.com | Test5 Bot   | Yes         | Default location is "Metro Detroit"
  test-a1@servuno.com
  test-a2@servuno.com
  

Notes
---------------

Unfulfilled tests are documented on Workflowy. Make sure to manually test those as well. Some of them are documented in the test cases with "todo" comment.


Tags
---------------

  * `@core`: the absolute essential things to test on all conditions
  * `@local`: make sure to test on local environment
  * `@live`: make sure to test on live environment
  * `@dev`: for development purpose only, should use ~@dev when do real testing. 
  

Steps
---------------

```
default |  When I open the recent email: :index
default |  When I open the last email
default |  Then (I )break
default |  Then show email content
default |  Then show email parsed content
default |  Then check email sent from :from_email to :to_email
default |  Then check email contains :text
default |  Then check email subject contains :text
default |  When I follow the email link like :link_pattern
default | Given I am logged in as user :user with password :password
default | Given I am logged in as admin
default |  Then /^take a screenshot$/
default |  Then /^save last response$/
default |  Then print the setting :key
default |  Then /^pause (?P<seconds>\d+) second(s?)$/
default |  When I run the following Javascript:
default | Given /^(?:|I )am on (?:|the )homepage$/
default |  When /^(?:|I )go to (?:|the )homepage$/
default | Given /^(?:|I )am on "(?P<page>[^"]+)"$/
default |  When /^(?:|I )go to "(?P<page>[^"]+)"$/
default |  When /^(?:|I )reload the page$/
default |  When /^(?:|I )move backward one page$/
default |  When /^(?:|I )move forward one page$/
default |  When /^(?:|I )press "(?P<button>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )follow "(?P<link>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )fill in "(?P<field>(?:[^"]|\\")*)" with "(?P<value>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )fill in "(?P<field>(?:[^"]|\\")*)" with:$/
default |  When /^(?:|I )fill in "(?P<value>(?:[^"]|\\")*)" for "(?P<field>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )fill in the following:$/
default |  When /^(?:|I )select "(?P<option>(?:[^"]|\\")*)" from "(?P<select>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )additionally select "(?P<option>(?:[^"]|\\")*)" from "(?P<select>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )check "(?P<option>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )uncheck "(?P<option>(?:[^"]|\\")*)"$/
default |  When /^(?:|I )attach the file "(?P<path>[^"]*)" to "(?P<field>(?:[^"]|\\")*)"$/
default |  Then /^(?:|I )should be on "(?P<page>[^"]+)"$/
default |  Then /^(?:|I )should be on (?:|the )homepage$/
default |  Then /^the (?i)url(?-i) should match (?P<pattern>"(?:[^"]|\\")*")$/
default |  Then /^the response status code should be (?P<code>\d+)$/
default |  Then /^the response status code should not be (?P<code>\d+)$/
default |  Then /^(?:|I )should see "(?P<text>(?:[^"]|\\")*)"$/
default |  Then /^(?:|I )should not see "(?P<text>(?:[^"]|\\")*)"$/
default |  Then /^(?:|I )should see text matching (?P<pattern>"(?:[^"]|\\")*")$/
default |  Then /^(?:|I )should not see text matching (?P<pattern>"(?:[^"]|\\")*")$/
default |  Then /^the response should contain "(?P<text>(?:[^"]|\\")*)"$/
default |  Then /^the response should not contain "(?P<text>(?:[^"]|\\")*)"$/
default |  Then /^(?:|I )should see "(?P<text>(?:[^"]|\\")*)" in the "(?P<element>[^"]*)" element$/
default |  Then /^(?:|I )should not see "(?P<text>(?:[^"]|\\")*)" in the "(?P<element>[^"]*)" element$/
default |  Then /^the "(?P<element>[^"]*)" element should contain "(?P<value>(?:[^"]|\\")*)"$/
default |  Then /^the "(?P<element>[^"]*)" element should not contain "(?P<value>(?:[^"]|\\")*)"$/
default |  Then /^(?:|I )should see an? "(?P<element>[^"]*)" element$/
default |  Then /^(?:|I )should not see an? "(?P<element>[^"]*)" element$/
default |  Then /^the "(?P<field>(?:[^"]|\\")*)" field should contain "(?P<value>(?:[^"]|\\")*)"$/
default |  Then /^the "(?P<field>(?:[^"]|\\")*)" field should not contain "(?P<value>(?:[^"]|\\")*)"$/
default |  Then /^the "(?P<checkbox>(?:[^"]|\\")*)" checkbox should be checked$/
default |  Then /^the checkbox "(?P<checkbox>(?:[^"]|\\")*)" (?:is|should be) checked$/
default |  Then /^the "(?P<checkbox>(?:[^"]|\\")*)" checkbox should not be checked$/
default |  Then /^the checkbox "(?P<checkbox>(?:[^"]|\\")*)" should (?:be unchecked|not be checked)$/
default |  Then /^the checkbox "(?P<checkbox>(?:[^"]|\\")*)" is (?:unchecked|not checked)$/
default |  Then /^(?:|I )should see (?P<num>\d+) "(?P<element>[^"]*)" elements?$/
default |  Then /^print current URL$/
default |  Then /^print last response$/
default |  Then /^show last response$/
```