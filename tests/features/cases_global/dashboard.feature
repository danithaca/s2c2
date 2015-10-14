Feature: check dashboard

  @core
  Scenario: dashboard links
    Given I am logged in as user "test@servuno.com" with password "password"
    Then I should be on ":LOGIN_LANDING"
    Given I am on "/dashboard/"
    Then I should see "Dashboard"
    And I should see "Build Network"
    And I should see "Post Job"

    When I follow "Build Network"
    Then I should see "Connect to parents"
    And I should see "Add Babysitters"
    Then I should be on "/connect/parent/"
    When I follow "Add Babysitters"
    Then I should be on "/connect/sitter/"

    When I move backward one page
    When I follow "Post Job"
    Then I should see "Find a Parent"
    And I should see "Book a Babysitter"
    Then I should be on "/job/post/favor/"
    When I follow "Book a Babysitter"
    Then I should be on "/job/post/paid/"

