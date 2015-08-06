Feature: sign up
  In order to start using servuno
  As an anonymous user
  I need to be able to signup

  @core
  Scenario: basic sign up
#    Given I am on the homepage
#    When I press "Sign Up"

    # first sign up page
    Given I am on "/account/signup/"
    When I fill in the following:
      | Email            | to-be-deleted@servuno.com |
      | Password         | password                  |
      | Password (again) | password                  |
    And I press "Sign up"
    Then I should be on "/account/onboard/profile/"
    And I should see "Confirmation email sent to to-be-deleted@servuno.com"


  @core
  Scenario: check confirmation email
    When I open the latest email
    Then check email subject contains "Confirm email address"
    When I follow the email link like "/account/confirm_email"
    Then I should see "Confirm email address to-be-deleted@servuno.com?"
    When I press "Confirm"
    Then I should see "You have confirmed to-be-deleted@servuno.com."


  @core
  Scenario: Clean up
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"
