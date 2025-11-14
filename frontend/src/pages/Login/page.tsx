import AuthLayout from './components/AuthLayout';
import LoginForm from './components/LoginForm';

const LoginPage = () => {
  return (
    <AuthLayout title="Log in to your account">
      <LoginForm />
    </AuthLayout>
  );
};

export default LoginPage;