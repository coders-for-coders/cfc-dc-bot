import mongoose, { Document } from "mongoose";

interface IUser extends Document {
    userId: string;
    credits: {
        image: number;
        text: number;
    };
}

const userSchema = new mongoose.Schema({
    userId: { type: String, required: true, unique: true },
    credits: {
        image: { type: Number, default: 3 },
        text: { type: Number, default: 10 },
    },
});

export const UserModel = mongoose.model<IUser>("User", userSchema);
