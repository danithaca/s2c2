Feature: Check link
  In order to view the information on the site
  As an anonymous user
  I need to view the links correctly

  @core
  Scenario: anonymous landing
    Given I am on the homepage
    Then the response status code should be 200
    Then I should be on ":ANONYMOUS_LANDING"
    And I should see "Ann Arbor"

    When I follow "Log In"
    Then I should be on "/account/login/"
    When I move backward one page
    And I follow "Sign Up"
    Then I should be on "/account/join/"


  @core @javascript
  Scenario: check jotform
    Given I am on the homepage
    Then pause 5 seconds
    And I should see a ".jotform-feedback-link" element
    And I should see "Send Feedback"
