Feature: Test manage public circles

  @core
  Scenario: basic manage interface is there
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/circle/manage/public"
    Then the response status code should be 200
    And I should see a ".public-circle-superset" element
    And I should see a ".public-circle-entity" element
    And I should see "Sleeping Bears"


  @javascript @core
  Scenario: add and remove, submit and check email
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/circle/manage/public"
    Then I should not see "Changes are not saved."

    # make sure it's unsubscribed.
    When I run the following Javascript:
      """
      $('li[data-slug="sleeping-bears"] input').bootstrapSwitch('state', false);
      """
    And I press "Save Changes"
    And I should be on "/account/"
    And I should not see "Sleeping Bears"

    # now let's subscribe it
    Given I am on "/circle/manage/public"
    When I run the following Javascript:
      """
      $('li[data-slug="sleeping-bears"] input').bootstrapSwitch('state', true);
      """
    Then I should see "Changes are not saved."
    And I press "Save Changes"
    And I should be on "/account/"
    And I should see "Sleeping Bears"

    # check email
    When I open the last email
    Then check email sent to "admin@servuno.com"
    And check email subject contains "Approval"
    And check email subject contains "Sleeping Bears"

    # test unsubscribe. the first time was just to make sure it wasn't already subscribed to setup to test subscribe.
    Given I am on "/circle/manage/public"
    When I run the following Javascript:
      """
      $('li[data-slug="sleeping-bears"] input').bootstrapSwitch('state', false);
      """
    Then I should see "Changes are not saved."
    And I press "Save Changes"
    And I should be on "/account/"
    And I should not see "Sleeping Bears"
