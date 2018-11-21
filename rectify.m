function rectify(img)
    I = imread(img);
    K = scan(I);
    string_len = strlength(img);
    newStr = eraseBetween(img, string_len-3, string_len);
    newStr = insertAfter(newStr, strlength(newStr), '_rectified.jpg');
    disp(newStr);
    imwrite((K), newStr); 
end
function [K] = scan(I)
    image(I);
    [xc,yc] = ginput(4);
    H = homography(xc, yc);
    J = warp(inv(H), I);
    [u.x, u.y] = upper_point(xc, yc);
    [l.x, l.y] = lower_point(xc, yc);
    U = H\[u.x; u.y; 1];
    L = H\[l.x; l.y; 1];
    U = [U(1)/U(3); U(2)/U(3)];
    L = [L(1)/L(3); L(2)/L(3)];
    [K, ~] = imcrop(J, [U(1) U(2) L(1)-U(1) L(2)-U(2)]);
end

function [x,y] = upper_point(xc, yc)
    x = xc(1);
    y = yc(1);
end

function [x,y] = lower_point(xc, yc)
    x = xc(3);
    y = yc(3);
end

function H = homography(xc, yc)
    xr = [min(xc), max(xc), max(xc), min(xc)];
    yr = [min(yc), min(yc), max(yc), max(yc)];
    A = [xr(1) yr(1) 1 0     0     0 -xr(1)*xc(1) -yr(1)*xc(1);
         0     0     0 xr(1) yr(1) 1 -xr(1)*yc(1) -yr(1)*yc(1);
         xr(2) yr(2) 1 0     0     0 -xr(2)*xc(2) -yr(2)*xc(2);
         0     0     0 xr(2) yr(2) 1 -xr(2)*yc(2) -yr(2)*yc(2);
         xr(3) yr(3) 1 0     0     0 -xr(3)*xc(3) -yr(3)*xc(3);
         0     0     0 xr(4) yr(3) 1 -xr(3)*yc(3) -yr(3)*yc(3);
         xr(4) yr(4) 1 0     0     0 -xr(4)*xc(4) -yr(4)*xc(4);
         0     0     0 xr(4) yr(4) 1 -xr(4)*yc(4) -yr(4)*yc(4)];
    b = [xc(1); yc(1); xc(2); yc(2); xc(3); yc(3); xc(4); yc(4)];
    hzinho = A\b;
    H = [hzinho(1) hzinho(2) hzinho(3); hzinho(4) hzinho(5) hzinho(6); hzinho(7) hzinho(8) 1];
end

function J = warp(H, I)

    [Uo,Vo] = imeshgrid(I);
    
    p = [Uo(:) Vo(:)]';
    p = [p; ones(1,numcols(p))];
    
    UV = convert(H\p);

    U = reshape(UV(1,:), size(Uo));
    V = reshape(UV(2,:), size(Vo));

    for channel=1:size(I,3)
        J(:,:,channel) = interp2(Uo, Vo, idouble(I(:,:,channel)), U, V, 'bilinear');
    end
end

function C = convert(M)
    s = size(M,2);
    for i = 1:s
        C(1, i) = M(1,i)/M(3,i);
        C(2, i) = M(2,i)/M(3,i);
    end
end

function [m,s] = stat2(x)
n = length(x);
m = avg(x,n);
s = sqrt(sum((x-m).^2/n));
end

