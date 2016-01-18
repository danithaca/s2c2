Feature: contact a user on the page

  @core
  Scenario: send message
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "View account"
    Then I should be on "/account/"
    And I should see "Test1 Bot"
    When I follow "Test1 Bot"
    Then I should see "Message"
    When I follow "Message"
    Then the url should match "/message/user/"
    When I fill in "body" with "hello world"
    And I press "Send"
    Then I should see "successful"
    And the url should match "/account/"
    And I should see "Message"


  Scenario: check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "sent you a message"
    And check email contains "hello world"
