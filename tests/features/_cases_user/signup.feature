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
    Then I should be on ":SIGNUP_LANDING"
    And I should see "Confirmation email sent to to-be-deleted@servuno.com"


  Scenario: check confirmation email
    When I open the last email from "admin@servuno.com" to "to-be-deleted@servuno.com"
    Then check email subject contains "Confirm email address"
    When I follow the email link like "/account/confirm_email"
    Then I should see "Confirm email address to-be-deleted@servuno.com?"
    When I press "Confirm"
    Then I should see "You have confirmed to-be-deleted@servuno.com."


  @core
  Scenario: check onboarding steps
    Given I am logged in as user "to-be-deleted@servuno.com" with password "password"
    Then I should be on ":SIGNUP_LANDING"
    And I should see "About Servuno"
    And I should see "Key Features"

    When I follow "Next"
    Then I should be on "/account/onboard/profile/"
    And I should see "Update Profile"
    When I fill in the following:
      | First name | Deleted              |
      | Last name  | Bot                  |
    And I press "Next"
    Then I should see "Profile successfully updated"

    Then I should be on "/account/onboard/parent/"
    And I should see "Connect to Parents"
    And I should see a "#new-item" element
    And I should see a "#new-item-add-btn" element
    When I press "Next"

    Then I should be on "/account/onboard/sitter/"
    And I should see "Add Paid Babysitters"
    And I should see a "#new-item" element
    And I should see a "#new-item-add-btn" element
    When I press "Next"

    Then I should be on ":LOGIN_LANDING"
    And I should see "Welcome!"
    And I should see "Deleted"


  @javascript @core
  Scenario: check new user login
    Given I am logged in as user "to-be-deleted@servuno.com" with password "password"
    Then I should be on "/dashboard/"
    Then I should see "End Tour"


  @javascript
  Scenario: check ui
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on ":SIGNUP_LANDING"
    Then I should see "Step 1"
    Then I should see "Step 2"
    Then I should see "Step 3"
    Then I should see "Step 4"
    And I should see a "#onboard-pane" element
    When I evaluate the following Javascript:
      """
      return $('li[data-slug="step-1"]').hasClass('active') && $('li[data-slug="step-2"]').hasClass('disabled');
      """
    Then check Javascript result is true

    When I follow "Next"
    When I evaluate the following Javascript:
      """
      return !($('li[data-slug="step-1"]').hasClass('active')) &&  $('li[data-slug="step-2"]').hasClass('active') && $('li[data-slug="step-3"]').hasClass('disabled')
      """
    Then check Javascript result is true

    Given I am on homepage
    And I set browser mobile
    And I am on ":SIGNUP_LANDING"
    Then I should not see "Step 2"
    And I should see "Step 1/4"


  @core
  Scenario: clean up
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"
