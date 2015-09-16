Feature: test choose audience feature in "find"

  @javascript
  Scenario: choose family helper audience
    Given I am logged in as user "test@servuno.com" with password "password"

    # make sure to subscribe to family helpers
    Given I am on "/circle/manage/agency"
    When I run the following Javascript:
      """
      $('li[data-slug="university-of-michigan-family-helpers"] input').bootstrapSwitch('state', true);
      """
    And I press "Save Changes"
    And I should see "University of Michigan Family Helpers"

    Given I am on "/contract/add/"
    When I fill in "price" with "10"
    Then the "price-info" field should contain "$10.00/hour, 1 hour"

    When I select "University of Michigan Family Helpers" from "audience"

    When I press "Submit"
    And I press "OK"
    Then the URL should match "/contract/\d+/"
    And I should see a ".match-summary" element

    # the rest might be hidden.
    And the response should contain "University of Michigan Family Helpers"
    And I should not see "John Smith's list"


  @javascript
  Scenario: choose public
    # make sure another person is in sleeping bears
    Given I am logged in as user "test1@servuno.com" with password "password"
    Given I am on "/circle/manage/public"
    When I run the following Javascript:
      """
      $('li[data-slug="sleeping-bears"] input').bootstrapSwitch('state', true);
      """
    And I press "Save Changes"
    And I should see "Sleeping Bears"

    Given I am on "/account/logout/"
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on "/circle/manage/public/"
    When I run the following Javascript:
      """
      $('li[data-slug="sleeping-bears"] input').bootstrapSwitch('state', true);
      """
    And I press "Save Changes"
    And I should see "Sleeping Bears"

    Given I am on "/contract/add/"
    When I fill in "price" with "10"
    Then the "price-info" field should contain "$10.00/hour, 1 hour"

    When I select "Sleeping Bears" from "audience"

    When I press "Submit"
    And I press "OK"
    Then the URL should match "/contract/\d+/"
    And I should see a ".match-summary" element

    And I should see "test1"
    And I should see "Sleeping Bears"
    And I should not see "John Smith's list"


  @javascript
  Scenario: choose personal
    Given I am logged in as user "test@servuno.com" with password "password"

    Given I am on "/contract/add/"
    When I fill in "price" with "10"
    Then the "price-info" field should contain "$10.00/hour, 1 hour"

    When I select "John Smith's list" from "audience"

    When I press "Submit"
    And I press "OK"
    Then the URL should match "/contract/\d+/"
    And I should see a ".match-summary" element

    And I should see "test1"
    And I should see "John Smith's list"
    And I should not see "Sleeping Bears"
    And I should not see "Family Helpers"



