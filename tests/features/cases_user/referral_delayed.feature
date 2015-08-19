Feature: Test referral user when the user doesn't signup right away
  In order to use servuno
  As a referred user who doesn't sign up right away
  I need to be able to use the site even without signed up first.

  @javascript
  Scenario: set up stage
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/circle/manage/personal/"
    Then I should not see "to-be-deleted-referral-delayed@servuno.com"
    When I fill in "new-contact" with "to-be-deleted-referral-delayed@servuno.com"
    And I press "new-contact-add-btn"
    Then I should see "to-be-deleted-referral-delayed@servuno.com"
    When I press "Submit"
    Then I should be on "/account/"
    Then I should see "to-be-deleted-referral-delayed@servuno.com"

    Given I am on "/contract/add/"
    When I fill in the following:
      | event_start | 12/02/2010 18:00 |
      | event_end   | 12/02/2010 19:00 |
      | price       | 8                |
    When I press "submit"
    Then the URL should match "/contract/\d+/"
    And I should see a ".match-summary" element
    And I should see "successfully"


  @javascript
  Scenario: create contract, check email/signup
    When I open the last email from "test@servuno.com" to "to-be-deleted-referral-delayed@servuno.com"
    Then show email content
    And check email subject contains "needs your help"
    And check email subject contains "John Smith"
    And check email contains "You do not have an active user account on Servuno"
    When I follow the email link like "/account/signup/"
    Then I should be on "/account/signup/"
    And the "Email" field should contain "to-be-deleted-referral-delayed@servuno.com"


  @javascript
  Scenario: clean up - remove from circle
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/circle/manage/personal/"
    When I run the following Javascript:
      """
      $('li[data-email="to-be-deleted-referral-delayed@servuno.com"] i.fa-remove').click();
      """
    Then I should not see "to-be-deleted-referral-delayed@servuno.com"

  Scenario: clean up - remove user
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-referral-delayed"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"