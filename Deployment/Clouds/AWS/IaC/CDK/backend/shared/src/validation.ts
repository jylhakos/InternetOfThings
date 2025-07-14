import Joi from 'joi';

export const createUserSchema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30).required(),
  email: Joi.string().email().required(),
  phoneNumber: Joi.string().pattern(/^\+?[1-9]\d{1,14}$/).required(),
  password: Joi.string().min(6).max(128).required()
});

export const signInSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

export const updateUserSchema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30),
  email: Joi.string().email(),
  phoneNumber: Joi.string().pattern(/^\+?[1-9]\d{1,14}$/)
}).min(1);

export const validateCreateUser = (data: any) => createUserSchema.validate(data);
export const validateSignIn = (data: any) => signInSchema.validate(data);
export const validateUpdateUser = (data: any) => updateUserSchema.validate(data);
