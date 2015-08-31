Feature: view newly created contract

  @core
  Scenario: view upcoming
    # assuming after the first step of creating a contract (nearest time), we would see that same contract.
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on the homepage
    And I should see an ".engagement" element
    And I should see "$10"


  @core @javascript
  Scenario: view contract
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on the homepage
    When I run the following Javascript:
      """
      $('.engagement.engagement-headline').click();
      """
    Then the URL should match "/contract/\d+/"
    And I should see "Edit"
    And I should see "Active"
    And I should see "Cancel"
    And I should see "Last updated"
    And I should see "test1"
    And I should see "John Smith's List"

    # didn't find a server yet, so there's no link to user page.
#    Given I am on the homepage
#    When I run the following Javascript:
#      """
#      $('.engagement.engagement-headline a.user-link').click();
#      """
#    Then the URL should match "/account/\d+/"