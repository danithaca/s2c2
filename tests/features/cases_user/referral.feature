Feature: Test referral user
  In order to use servuno
  As a referred user
  I need to be able to sign up.

  @javascript
  Scenario: set up stage
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/circle/manage/personal"
    Then I should not see "to-be-deleted-referral@servuno.com"
    When I fill in "new-contact" with "to-be-deleted-referral@servuno.com"
    And I press "new-contact-add-btn"
    Then I should see "to-be-deleted-referral@servuno.com"
    When I press "Submit"
    Then I should be on "/account/"
    Then I should see "to-be-deleted-referral@servuno.com"


  @javascript
  Scenario: check dummy user account
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-referral"
    Then the checkbox "Active" should be checked
    And the checkbox "Is user registered" should not be checked
    And the checkbox "Primary" should be checked
    And the checkbox "Verified" should not be checked
    And the "Email" field should contain "to-be-deleted-referral@servuno.com"
    # we assume 1 is always present in a 64 length string
    # And the "Token" field should contain "1"
    When I evaluate the following Javascript:
      """
      return document.getElementById('id_token-0-token').value.length == 64;
      """
    Then check Javascript result is true


  @javascript
  Scenario: follow sign up step
    When I open the last email
    Then show email content
    And check email subject contains "invited"
    And check email sent from "admin@servuno.com" to "to-be-deleted-referral@servuno.com"
    When I follow the email link like "/account/signup/?code="
    Then I should be on "/account/signup/"
    And the "Email" field should contain "to-be-deleted-referral@servuno.com"

    When I fill in the following:
      | Password         | password |
      | Password (again) | password |
    And I press "Sign up"
    Then I should be on "/account/onboard/profile/"

    When I fill in the following:
      | First name | 2BD |
      | Last name  | Bot |
    And I press "Next >"
    Then I should be on "/account/onboard/personal/"
    # if this is the referred user, by default the referrer should appear here.
    And I should see "test@servuno.com"

    When I press "Next >"
    Then I should be on "/account/onboard/public/"
    When I press "Next >"
    Then I should be on "/account/onboard/picture/"
    When I press "Next >"
    Then I should be on "/calendar/"

    Given I am on "/circle/manage/personal/"
    Then I should see "test@servuno.com"

    Given I am on "/account/"
    Then the response should contain "test@servuno.com"


  @javascript
  Scenario: clean up - remove from circle
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/circle/manage/personal/"
    When I run the following Javascript:
      """
      $('li[data-email="to-be-deleted-referral@servuno.com"] i.fa-remove').click();
      """
    Then I should not see "to-be-deleted-referral@servuno.com"

  Scenario: clean up - remove user
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-referral"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"