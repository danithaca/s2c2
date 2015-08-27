Feature: pre registered user
  In order to use the site without "signing up" (perhaps through referral)
  As a pre registered user
  I need to do some basic stuff regarding my account.

  @javascript
  Scenario: set up stage
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/circle/manage/personal"
    Then I should not see "to-be-deleted-dummy@servuno.com"
    When I fill in "new-contact" with "to-be-deleted-dummy@servuno.com"
    And I press "new-contact-add-btn"
    Then I should see "to-be-deleted-dummy@servuno.com"
    When I press "Submit"
    Then I should be on "/account/"
    Then I should see "to-be-deleted-dummy@servuno.com"


  @javascript
  Scenario: check dummy user account
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-dummy"
    Then the checkbox "Active" should be checked
    And the checkbox "Is user registered" should not be checked
    And the checkbox "Primary" should be checked
    And the checkbox "Verified" should not be checked
    And the "Email" field should contain "to-be-deleted-dummy@servuno.com"
    # we assume 1 is always present in a 64 length string
    # And the "Token" field should contain "1"
    When I evaluate the following Javascript:
      """
      return document.getElementById('id_token-0-token').value.length == 64;
      """
    Then check Javascript result is true

  Scenario: sign up
    Given I am on "/account/signup/"
    When I fill in the following:
      | Email            | to-be-deleted-dummy@servuno.com |
      | Password         | password                        |
      | Password (again) | password                        |
    And I press "Sign up"
    Then I should be on ":SIGNUP_LANDING"


  Scenario: test after sign up
    Given I am on "/account/signup/"
    When I fill in the following:
      | Email            | to-be-deleted-dummy@servuno.com |
      | Password         | password                        |
      | Password (again) | password                        |
    And I press "Sign up"
    Then I should see "A user is registered with this email address."
    And I should be on "/account/signup/"

    Given I am on "/account/login/"
    When I fill in the following:
      | Email            | to-be-deleted-dummy@servuno.com |
      | Password         | password                        |
    And I press "Log in"
    Then the response status code should be 200
    And the response should contain "<!-- logged in as to-be-deleted-dummy@servuno.com -->"


  Scenario: clean up - remove user
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-dummy"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"  