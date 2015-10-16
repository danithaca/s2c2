Feature: check dashboard

  @core
  Scenario: dashboard top links
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


  @core
  Scenario: dashboard user links
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "link_dashboard_picture"
    Then I should be on "/account/picture/"

    When I move backward one page
    When I follow "link_dashboard_account_view"
    Then I should be on "/account/"

    When I move backward one page
    When I follow "link_dashboard_account_edit"
    Then I should be on "/account/edit/"

    When I move backward one page
    Then I should see a ".user-level" element
    And I should see a "#list-activities" element
    And I should see a "#list-interactions" element
    And I should see a ".engagement-feed" element


  @core @javascript
  Scenario: dashboard js stuff
    Given I am logged in as user "test@servuno.com" with password "password"
    Then I should see a ".engagement-feed" element
    When I click the ".engagement-feed" element
    Then the url should match "/job/.*/"

    When I move backward one page
    When I click the "#list-interactions" element
    Then I should see a ".interactions-label" element