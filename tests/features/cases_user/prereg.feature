Feature: pre registered user
  In order to use the site without "signing up" (perhaps through referral)
  As a pre registered user
  I need to do some basic stuff regarding my account.

  @javascript
  Scenario: set up stage
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/connect/parent/"
    Then I should not see "to-be-deleted-dummy@servuno.com"
    When I fill in "new-item" with "to-be-deleted-dummy@servuno.com to-be-deleted-dummy2@servuno.com"
    And I press "new-item-add-btn"
    Then I should see "to-be-deleted-dummy@servuno.com"
    When I press "Save Changes"
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


  Scenario: forget password and then login
    Given I am on "/account/login/"
    When I fill in the following:
      | Email            | to-be-deleted-dummy2@servuno.com |
      | Password         | password                         |
    And I press "Log in"
    Then I should see "The email address and/or password you specified are not correct."
    When I follow "Forget password?"
    Then I should see "Password reset"
    When I fill in "to-be-deleted-dummy2@servuno.com" for "Email"
    And I press "Request"

    # check email
    Then pause 2 seconds
    When I open the last email
    Then check email sent to "to-be-deleted-dummy2@servuno.com"
    And check email contains "/account/password/reset/"

    When I follow the email link like "/account/password/reset/"
    Then I should see "Set your new password"

    When I fill in the following:
      | New Password         | password |
      | New Password (again) | password |
    And I press "Reset"
    Then I should see "Password successfully changed."

    Given I am on "/account/logout/"
    Given I am on "/account/login/"
    When I fill in the following:
      | Email            | to-be-deleted-dummy2@servuno.com |
      | Password         | password                         |
    And I press "Log in"
    Then the response status code should be 200
    And the response should contain "<!-- logged in as to-be-deleted-dummy2@servuno.com -->"


  Scenario: clean up - remove user
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-dummy"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"
    When I follow "to-be-deleted-dummy2"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"
