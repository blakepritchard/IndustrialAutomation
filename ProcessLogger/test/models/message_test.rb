require 'test_helper'

class MessageTest < ActiveSupport::TestCase
  test "the truth" do
    assert true
  end

  test "should not save message without Process" do
    message = Message.new
    assert !message.save, "Saved a Message without a Process"
  end

  test "should not save message without Sender" do
    message = Message.new
    assert !message.save, "Saved a Message without a Sender"
  end

end
