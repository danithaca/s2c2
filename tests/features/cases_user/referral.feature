Feature: Test referral user
  In order to use servuno
  As a referred user
  I need to be able to sign up.

  @javascript
  Scenario: set up stage
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/connect/parent/"
    Then I should not see "to-be-deleted-referral@servuno.com"
    When I fill in "new-item" with "to-be-deleted-referral@servuno.com"
    And I press "new-item-add-btn"
    Then I should see "to-be-deleted-referral@servuno.com"
    When I press "Save Changes"
    Then I should see "to-be-deleted-referral@servuno.com"


  @javascript
  Scenario: follow sign up step
    # give it a few seconds to response
    Then pause 3 seconds
    When I open the last email from "test@servuno.com" to "to-be-deleted-referral@servuno.com"
    And check email subject contains "connected"
    When I follow the email link like "account/signup/?token="
    Then I should be on "/account/signup/"
    And the "Email" field should contain "to-be-deleted-referral@servuno.com"

    When I fill in the following:
      | Password         | password |
      | Password (again) | password |
    And I press "Sign up"
    Then I should be on ":SIGNUP_LANDING"
    When I follow "Next"
    Then I should be on "/account/onboard/profile/"
    When I fill in the following:
      | First name | 2BD |
      | Last name  | Bot |
    When I press "Next"

    Then I should be on "/account/onboard/parent/"
    # if this is the referred user, by default the referrer should appear here.
    And I should see "John Smith"

    When I press "Next"
    Then I should be on "/account/onboard/sitter/"
    When I press "Next"
    Then I should be on ":LOGIN_LANDING"

    Given I am on "/connect/parent/"
    Then I should see "John Smith"

    Given I am on "/account/"
    Then the response should contain "test@servuno.com"


  @javascript
  Scenario: clean up - remove from circle
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/connect/parent/"
    When I click the "li[data-email='to-be-deleted-referral@servuno.com'] .destroy" element
    Then I should not see "to-be-deleted-referral@servuno.com"

  Scenario: clean up - remove user
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-referral"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"