import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { connectToDatabase } from './mongodb';

export interface User {
    _id?: string;
    name: string;
    email: string;
    password: string;
    createdAt: Date;
    updatedAt: Date;
}

export interface AuthResponse {
    success: boolean;
    user?: Omit<User, 'password'>;
    token?: string;
    message?: string;
}

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

export async function hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 12);
}

export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
    return bcrypt.compare(password, hashedPassword);
}

export function generateToken(userId: string): string {
    return jwt.sign({ userId }, JWT_SECRET, { expiresIn: '7d' });
}

export function verifyToken(token: string): { userId: string } | null {
    try {
        return jwt.verify(token, JWT_SECRET) as { userId: string };
    } catch {
        return null;
    }
}

export async function createUser(name: string, email: string, password: string): Promise<AuthResponse> {
    try {
        const { db } = await connectToDatabase();
        const users = db.collection<User>('users');

        // Check if user already exists
        const existingUser = await users.findOne({ email: email.toLowerCase() });
        if (existingUser) {
            return { success: false, message: 'User already exists with this email' };
        }

        // Hash password and create user
        const hashedPassword = await hashPassword(password);
        const newUser: Omit<User, '_id'> = {
            name,
            email: email.toLowerCase(),
            password: hashedPassword,
            createdAt: new Date(),
            updatedAt: new Date(),
        };

        const result = await users.insertOne(newUser);
        const user = await users.findOne({ _id: result.insertedId });

        if (!user) {
            return { success: false, message: 'Failed to create user' };
        }

        const token = generateToken(user._id.toString());
        const { password: _, ...userWithoutPassword } = user;

        return {
            success: true,
            user: { ...userWithoutPassword, _id: user._id.toString() },
            token,
        };
    } catch (error) {
        console.error('Create user error:', error);
        return { success: false, message: 'Internal server error' };
    }
}

export async function authenticateUser(email: string, password: string): Promise<AuthResponse> {
    try {
        const { db } = await connectToDatabase();
        const users = db.collection<User>('users');

        // Find user by email
        const user = await users.findOne({ email: email.toLowerCase() });
        if (!user) {
            return { success: false, message: 'Invalid email or password' };
        }

        // Verify password
        const isValidPassword = await verifyPassword(password, user.password);
        if (!isValidPassword) {
            return { success: false, message: 'Invalid email or password' };
        }

        const token = generateToken(user._id.toString());
        const { password: _, ...userWithoutPassword } = user;

        return {
            success: true,
            user: { ...userWithoutPassword, _id: user._id.toString() },
            token,
        };
    } catch (error) {
        console.error('Authenticate user error:', error);
        return { success: false, message: 'Internal server error' };
    }
}