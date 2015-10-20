Feature: offer help to other parents

  @core
  Scenario: access the link
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Post Job"
    And I follow "Offer Help"
    Then I should be on "/job/post/offer/"


  @javascript
  Scenario: form submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/job/post/offer/"
    When I fill in "description" with "i can help"
    When I press "Post"
    And I press "OK"
    Then the URL should match "/job/\d+/"
    And I should see a ".match-summary" element
    And I should see "successfully"


  Scenario: check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email contains "Template: contract/messages/match_engaged_reversed"
    Then check email subject contains "John Smith"
    And check email contains "reciprocity"
    And check email contains "/job/response/"


  @javascript
  Scenario: check "help offer"
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/dashboard/"
    Then I should see a ".engagement-feed" element
    When I arbitrarily click the ".engagement-feed:first" element
    Then the url should match "/job/\d+/"
    Then I should see "help offer"
