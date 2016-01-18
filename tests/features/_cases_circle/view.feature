Feature: view contacts

  @core
  Scenario: look at contacts on account
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "View account"
    Then I should be on "/account/"
    And I should see "Test1 Bot"
    When I follow "Test1 Bot"
    Then the url should match "/account/"
    When I move backward one page
    Then I should see "test3@servuno.com"
    When I follow "test3@servuno.com"
    Then the url should match "/account/"


  @javascript
  Scenario: attention icon and "isolated" tour message
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/dashboard/"
    Then I should not see "End Tour"
#    Then I should not see a ".tour-tour" element
#    Given I am on "/contract/add/"
#    Then I should not see "You have few contacts on Servuno. Please add more contacts and/or join more parents circles."
    Given I am on "/account/logout/"
    # this user is under represented.
    Given I am logged in as user "test2@servuno.com" with password "password"
    And I am on "/dashboard/"
    Then pause 5 seconds
    Then I should see "End Tour"
#    Then I should see a ".tour-tour" element
#    Given I am on "/contract/add/"
#    Then I should see "You have few contacts on Servuno. Please add more contacts and/or join more parents circles."