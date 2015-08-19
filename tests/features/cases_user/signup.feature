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


  Scenario: check confirmation email
    When I open the last email
    Then check email subject contains "Confirm email address"
    When I follow the email link like "/account/confirm_email"
    Then I should see "Confirm email address to-be-deleted@servuno.com?"
    When I press "Confirm"
    Then I should see "You have confirmed to-be-deleted@servuno.com."

  @core
  Scenario: check onboarding steps
    Given I am logged in as user "to-be-deleted@servuno.com" with password "password"
    Then I should be on "/account/onboard/profile/"
    When I fill in the following:
      | First name | Deleted              |
      | Last name  | Bot                  |
      | Phone      | 555-555-5556         |
      | Address    | 123 Someplace, Earth |
      | About me   | Blah                 |
    And I press "Next >"

    Then I should see "Profile successfully updated"
    And I should be on "/account/onboard/personal/"
    And I should see a "#new-contact" element
    And I should see a "#new-contact-add-btn" element

    When I press "Next >"
    Then I should be on "/account/onboard/public/"
    And I should see a ".public-circle-superset" element
    And I should see a ".public-circle-entity" element
    And I should see "Sleeping Bears"

    When I press "Next >"
    Then I should be on "/account/onboard/picture/"
    And I should see a "#id_picture_original" element
    # this perhaps needs javascript
    #And I should see "No file chosen"
    And I should see "Picture upload"

    When I press "Next >"
    Then I should be on "/calendar/"
    And I should see "Welcome!"
    And I should see "Deleted"

  @core
  Scenario: clean up
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"
