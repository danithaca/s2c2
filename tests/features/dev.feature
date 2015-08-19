Feature: development
  In order to test behat feature
  As a developer
  I need to run ad-hoc tests

  @dev
  Scenario: Test email
    Then show email content
    Then show email parsed content
    Then check email sent to "test@servuno.com"
    # Then check email sent from "admin@servuno.co" to "test@servuno.co"

    Then check email contains "because you or someone else"
#    Then check email contains "because you suck"

    Then check email subject contains "password reset"
#    Then check email subject contains "no password reset"

#    Then I follow the email link like "/account/"
#    Then I should see "Login"

    When I follow the email link like "/account/password/reset/"

#  @javascript
#  Scenario: Test fail
#    Given I am on "http://google.com"
#    Then I should see "hello, world"

  @dev
  Scenario: test new email
    # When I open the last email
    When I open the recent email: 2
    Then show email parsed content
    Then check email sent from "to-be-deleted-referral@servuno.com" to "test@servuno.com"

  @dev
  Scenario: print setting
    Then pause 5 seconds
    Then print the setting "contexts"