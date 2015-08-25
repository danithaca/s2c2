Feature: test login_token feature

  Scenario: login with token
    Given I am on "/account/"
    Then I should be on "/account/login/"

    Given I am on "/account/?login_token=d764cf49df021f42402cdb444999cf46ff81f13c66b5a594424778f0e7b7e69b"
    Then I should be on "/account/"
    And the response should contain "<!-- logged in as test@servuno.com -->"


  Scenario: login when another user is logged in
    Given I am logged in as user "test1@servuno.com" with password "password"
    Then the response should contain "<!-- logged in as test1@servuno.com -->"

    Given I am on "/account/?login_token=d764cf49df021f42402cdb444999cf46ff81f13c66b5a594424778f0e7b7e69b"
    Then I should be on "/account/"
    And the response should contain "<!-- logged in as test@servuno.com -->"
    And I should see "before login with token"


  Scenario: try invalid token and same token again
    Given I am on "/account/?login_token=abcd"
    Then I should be on "/account/login/"
    And I should see "invalid"

    Given I am on "/account/?login_token=d764cf49df021f42402cdb444999cf46ff81f13c66b5a594424778f0e7b7e69b"
    Then I should be on "/account/"
    And the response should contain "<!-- logged in as test@servuno.com -->"
    Given I am on "/account/?login_token=d764cf49df021f42402cdb444999cf46ff81f13c66b5a594424778f0e7b7e69b"
    Then I should be on "/account/"
    And the response should contain "<!-- logged in as test@servuno.com -->"
