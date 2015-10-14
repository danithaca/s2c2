Feature: connect to a user on that user's page

  @javascript @core
  Scenario: connect as parent
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on "/account/"
    Then I should see "Test1 Bot"
    When I follow "Test1 Bot"
    Then I should see "Connect"
    And I should see a "#user-connect-button" element
    When I click the "#user-connect-button" element
    Then I should see "Connect Test1 Bot"
    And the "parent_circle" checkbox should be checked
    When I uncheck "parent_circle"
    And I press "Update"
    Then I should see "successful"

    Given I am on "/connect/parent/"
    Then I should not see "Test1 Bot"
    When I fill in "new-item" with "test1@servuno.com"
    # we don't save it there, just to get the link to jump there
    And I press "new-item-add-btn"
    Then I should see "Test1 Bot"

    When I follow "Test1 Bot"
    When I click the "#user-connect-button" element
    Then the "parent_circle" checkbox should not be checked
    When I check "parent_circle"
    And I press "Update"
    Then I should see "successful"

    Given I am on "/connect/parent/"
    Then I should see "Test1 Bot"

  @javascript @core
  Scenario: connect as babysitter
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on "/account/"
    Then I should see "test3@servuno.com"
    When I follow "test3@servuno.com"
    Then I should see "Connect"
    And I should see a "#user-connect-button" element
    When I click the "#user-connect-button" element
    Then I should see "Connect test3@servuno.com"
    When I uncheck "sitter_circle"
    And I press "Update"

    Given I am on "/connect/sitter/"
    Then I should not see "test3@servuno.com"
    When I fill in "new-item" with "test3@servuno.com"
    # we don't save it there, just to get the link to jump there
    And I press "new-item-add-btn"
    Then I should see "test3@servuno.com"

    When I follow "test3@servuno.com"
    When I click the "#user-connect-button" element
    Then the "sitter_circle" checkbox should not be checked
    When I check "sitter_circle"
    And I press "Update"
    Then I should see "successful"

    Given I am on "/connect/sitter/"
    Then I should see "test3@servuno.com"
