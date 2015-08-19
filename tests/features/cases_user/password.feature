Feature: password change
  In order to login to servuno without a password
  As anonymous user
  I need to be able to reset my password

  @core
  Scenario: check link on homepage
    Given I am on the homepage
    Then I should see "Forget password?"
    When I follow "Forget password?"
    Then I should be on "account/password/reset/"


  Scenario: request and reset password
    Given I am on "account/login"
    Then I should see "Forget password?"
    When I follow "Forget password?"
    Then I should see "Password reset"
    When I fill in "test@servuno.com" for "Email"
    And I press "Request"
    Then I should see "We have sent you an email."

    # check email
    When I open the last email
    Then check email sent to "test@servuno.com"
    And check email contains "You're receiving this email because you or someone else has requested a password"
    And check email contains "/account/password/reset/"

    When I follow the email link like "/account/password/reset/"
    Then I should see "Set your new password"

    When I fill in the following:
      | New Password         | password1 |
      | New Password (again) | password1 |
    And I press "Reset"
    Then I should see "Password successfully changed."


  Scenario: change password
    Given I am on the homepage
    # note: using the new password.
    And I fill in the following:
      | Email    | test@servuno.com |
      | Password | password1        |
    And I press "Log in"
    Then the response should contain "<!-- logged in as test@servuno.com -->"

    # change password
    When I follow "Edit account"
    And I follow "Change password"
    And I fill in the following:
      | Current Password     | password1 |
      | New Password         | password  |
      | New Password (again) | password  |
    And I press "Change"
    Then I should see "Password successfully changed."

    When I open the last email
    Then check email sent to "test@servuno.com"
    And check email subject contains "Change password email notification"


  Scenario: request password again
    Given I am on "/account/password/reset/"
    When I fill in "test@servuno.com" for "Email"
    And I press "Request"
    Then I should see "We have sent you an email."
    When I press "Resend"
    Then I should see "If you still do not see the password reset email"


  Scenario: check bad token response
    Given I am on "/account/password/reset/2b-432-8e091cabdbc4960534dbxxx"
    Then I should see "Bad token"
