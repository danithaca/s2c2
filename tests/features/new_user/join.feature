Feature: sign up
  In order to start using servuno
  As an anonymous user
  I need to be able to signup using the "join" form

  @core
  Scenario: go to the "join" form
    Given I am on the homepage
    When I follow "Sign Up"
    Then I should be on "/account/join/"
    When I move backward one page
    And I follow "Sign Up Now!"
    Then I should be on "/account/join/"

  @core
  Scenario: fill out the join form with no valid token
    Given I am on "/account/join/"
    When I fill in "Email" with "subscribe@servuno.com"
    And I press "Sign Up"
    Then I should be on ":ANONYMOUS_LANDING"
    And I should see "Thank you" in the ".alert" element

    Given I am on "/account/join/"
    When I fill in "Email" with "subscribe@servuno.com"
    And I fill in "Invitation code" with "invalid"
    And I press "Sign Up"
    Then I should be on ":ANONYMOUS_LANDING"
    And I should see "Thank you" in the ".alert" element

    # check waiting list
    Given I am logged in as admin
    And I am on "/admin/puser/waiting/"
    Then I should see "subscribe@servuno.com"

    # remove it
    When I follow "subscribe@servuno.com"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Given I am on "/admin/puser/waiting/"
    And I should not see "subscribe@servuno.com"

  @core
  Scenario: sign up with valid code
    Given I am on "/account/join/"
    When I fill in "Email" with "subscribe@servuno.com"
    And I fill in "Invitation code" with "beta"
    And I press "Sign Up"
    Then I should be on ":SIGNUP_LANDING"
    And the "Email" field should contain "subscribe@servuno.com"