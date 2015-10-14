Feature: contact us

  @core
  Scenario: anynomous user
    Given I am on the homepage
    Then I should see "Contact Us"
    When I follow "Contact Us"
    Then I should be on "/message/feedback/"
    When I fill in "body" with "hello world"
    And I press "Send"
    Then I should be on ":ANONYMOUS_LANDING"


  Scenario: check email
    When I open the last email
    Then check email contains "hello world"
    And check email subject contains "Site feedback"

  @core
  Scenario: loggedin user
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on the homepage
    Then I should see "Contact Us"
    When I follow "Contact Us"
    Then I should be on "/message/feedback/"
    When I fill in "body" with "hello world"
    And I press "Send"
    Then I should be on ":LOGIN_LANDING"

  Scenario: check email
    When I open the last email
    Then Check email sent from "test@servuno.com" to "admin@servuno.com"
    Then check email contains "hello world"
    And check email subject contains "Site feedback"