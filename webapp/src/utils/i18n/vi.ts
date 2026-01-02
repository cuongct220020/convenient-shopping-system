import { i18nKeys } from './keys'

export const vi: Record<i18nKeys, string> = {
  invalid_email: 'Email không hợp lệ',
  invalid_username:
    'Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới (3-20 ký tự)',
  invalid_username_or_email: 'Email hoặc tên đăng nhập không hợp lệ',
  invalid_password: 'Mật khẩu phải chứa 6 ký tự trở lên',
  empty_password: 'Mật khẩu không được để trống',
  invalid_confirm_password: 'Mật khẩu xác nhận không khớp',
  empty_confirm_password: 'Mật khẩu xác nhận không được để trống',
  empty_username: 'Email hoặc tên đăng nhập không được để trống',
  empty_name: 'Vui lòng nhập họ và tên',
  invalid_name_length: 'Tên không được quá 50 ký tự',
  invalid_name_format: 'Tên chỉ được chứa chữ cái và khoảng trắng',
  name_requires_two_parts: 'Vui lòng nhập đầy đủ họ và tên',
  network_error: 'Lỗi kết nối mạng',
  error_occured: 'Đã xảy ra lỗi',
  internal_error: 'Có lỗi xảy ra, vui lòng thử lại sau',
  confirm: 'Đồng ý',
  decline: 'Hủy bỏ',
  incorrect_credentials: 'Sai thông tin đăng nhập',
  recheck_credentials: 'Vui lòng kiểm tra lại thông tin bạn đã nhập',
  register_success_title: 'Đăng ký thành công',
  register_login_to_continue: 'Vui lòng đăng nhập để tiếp tục',
  auth_failed: 'Xác thực thất bại',
  auth_succeeded: 'Xác thực thành công',
  otp_unverified: 'Mã xác nhận không đúng hoặc đã hết hạn. Vui lòng thử lại.',
  otp_verified: 'Xác thực tài khoản thành công. Vui lòng đăng nhập để tiếp tục',
  otp_expired: 'Mã xác thực đã hết hạn. Vui lòng thử lại',
  reset_password_success_title: 'Đổi mật khẩu thành công',
  reset_password_login_to_continue:
    'Mật khẩu của bạn đã được cập nhật, vui lòng đăng nhập bằng mật khẩu mới để tiếp tục.',
  storage_bulk: 'Kho chứa khác',
  storage_freezer: 'Tủ đông',
  storage_nonfreezer: 'Tủ thường',
  empty_storage_name: 'Tên kho chứa không được để trống',
  invalid_storage_name:
    'Tên kho chứa phải có ít nhất 3 ký tự, chỉ bao gồm chữ cái a-z, A-Z, chữ số 0-9 và kí tự "-", "_"'
}
