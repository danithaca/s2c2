Feature: Test manage loop (in other people's list)

  @core
  Scenario: basic manage interface is there
    Given I am logged in as user "test1@servuno.com" with password "password"
    And I am on "/circle/manage/loop"
    Then the response status code should be 200
    And I should see "Manage"
    And I should see a ".circle-loop" element
    And I should see "John Smith"


  @javascript
  Scenario: remove, submit
    Given I am logged in as user "test1@servuno.com" with password "password"
    And I am on "/circle/manage/loop"
    When I run the following Javascript:
      """
      $('li[data-slug="john-smith"] input').bootstrapSwitch('state', false);
      """
    And I press "Update"
    And I should be on "/account/"
    And I should not see "John Smith"

    # test@servuno.com still sees test1 as in the list. so we don't need to test there
    # might need to test some visual stuff

    # test unsubscribe. the first time was just to make sure it wasn't already subscribed to setup to test subscribe.
    Given I am on "/circle/manage/loop"
    When I run the following Javascript:
      """
      $('li[data-slug="john-smith"] input').bootstrapSwitch('state', true);
      """
    And I press "Update"
    And I should be on "/account/"
    And I should see "John Smith"
