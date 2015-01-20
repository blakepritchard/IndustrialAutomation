class MessagesController < ApplicationController
  skip_before_filter  :verify_authenticity_token

  def show
    @message = Message.find(params[:id])
  end

  def new

  end

  def create
    # render plain: params[:message].inspect
    @message = Message.new(message_params)

    @message.save
    redirect_to(@message)
  end

  private
    def message_params
      #params.require(:message).permit(:process, :sender, :text)
      params.permit(:process, :sender, :text, :adc1, :adc2, :adc3, :adc4, :adc5, :adc6, :adc7, :adc8)
    end

end
