Feature: check dashboard

  @core
  Scenario: dashboard links
    Given I am logged in as user "test@servuno.com" with password "password"
    Then I should be on ":LOGIN_LANDING"
    Given I am on "/dashboard/"

    When I follow "Find a Babysitter"
    Then I should be on "/contract/add/"

    When I move backward one page
    When I follow "View Activities"
    Then I should be on "/contract/calendar/"

    When I move backward one page
    When I follow "Manage Contacts"
    Then I should be on ":MANAGE_CONTACTS_DEFAULT"

    When I move backward one page
    When I follow "View Account"
    Then I should be on "/account/"

