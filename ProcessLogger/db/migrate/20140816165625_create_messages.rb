class CreateMessages < ActiveRecord::Migration
  def change
    create_table :messages do |t|
      t.string :process
      t.string :sender
      t.text :text

      t.timestamps
    end
  end
end
