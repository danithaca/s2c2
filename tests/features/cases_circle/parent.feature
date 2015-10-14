Feature: Test manage parent feature

  @core
  Scenario: basic manage interface is there
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/connect/parent/"
    Then the response status code should be 200
    And I should see "Connect to Parents"
    And I should see a "#new-item" element
    And I should see a "#new-item-add-btn" element

  @javascript @core
  Scenario: add and remove UI, does not submit
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/connect/parent/"
    Then I should not see "Changes are not saved."

    When I run the following Javascript:
      """
      $('div[data-email="test1@servuno.com"] .destroy').click();
      """
    Then I should not see "Test1 Bot"
    And I should see "Changes are not saved."

    When I run the following Javascript:
      """
      $('div[data-email="test2@servuno.com"] .destroy').click();
      """
    Then I should not see "Nancy Doe"

    When I fill in "new-item" with "test1@servuno.com test2@servuno.com"
    And I press "new-item-add-btn"
    Then I should see "Test1 Bot"
    And I should see "Nancy Doe"
    And I should see "Changes are not saved."

  @javascript @core
  Scenario: submit
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/connect/parent/"

    When I run the following Javascript:
      """
      $('div[data-email="test1@servuno.com"] .destroy').click();
      """
    Then I should not see "Test1 Bot"

    When I press "Save Changes"
    And I should be on "/connect/parent/"
    And I should not see "Test1 Bot"

    Given I am on "/connect/parent/"
    When I fill in "new-item" with "test1@servuno.com"
    And I press "new-item-add-btn"
    Then I should see "Test1 Bot"

    When I press "Save Changes"
    Then I should see "successfully updated"
    And I should be on "/connect/parent/"
    And I should see "Test1 Bot"

    When I follow "Test1 Bot"
    Then the url should match "/account/"

  Scenario: check email after submit
    # note: test1 should be "active", otherwise the email is "referral", tested in the other scenario
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "You are connected to"
    And check email contains "John Smith"