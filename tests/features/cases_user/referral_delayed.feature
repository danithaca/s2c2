Feature: Test referral user when the user doesn't signup right away
  In order to use servuno
  As a referred user who doesn't sign up right away
  I need to be able to use the site even without signed up first.

  @javascript
  Scenario: set up stage
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/connect/sitter/"
    Then I should not see "to-be-deleted-referral-delayed@servuno.com"
    When I fill in "new-item" with "to-be-deleted-referral-delayed@servuno.com"
    And I press "new-item-add-btn"
    Then I should see "to-be-deleted-referral-delayed@servuno.com"
    When I press "Save Changes"
    Then I should see "to-be-deleted-referral-delayed@servuno.com"

    Given I am on "/job/post/paid/"
    When I fill in the following:
      | event_start | 12/02/2020 18:00 |
      | event_end   | 12/02/2020 19:00 |
      | price       | 8                |
    When I press "Post"
    And I press "OK"
    Then the URL should match "/job/\d+/"
    And I should see a ".match-summary" element
    And I should see "successfully"


  @javascript
  Scenario: create contact, check email/signup
    When I open the last email from "test@servuno.com" to "to-be-deleted-referral-delayed@servuno.com"
    And check email subject contains "John Smith needs help babysitting (for a fee)"
    And check email contains "Sign up at"
    When I follow the email link like "/account/signup/"
    Then I should be on "/account/signup/"
    And the "Email" field should contain "to-be-deleted-referral-delayed@servuno.com"


#  @javascript
#  Scenario: clean up - remove from circle
#    Given I am logged in as user "test@servuno.com" with password "password"
#    And I am on "/connect/sitter/"
#    When I click the "li[data-email='to-be-deleted-referral-delayed@servuno.com'] .destroy" element
#    Then I should not see "to-be-deleted-referral-delayed@servuno.com"

  Scenario: clean up - remove user
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-referral-delayed"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"